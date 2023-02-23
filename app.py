from flask import Flask
import os
from volume_module import volume_bp
import logging
from extensions import celery
from datetime import timedelta
from utils import get_ec2_resource
from db import db
from volume_module.service import VolumeDbService


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MONGO_URI'] = os.environ.get("DB_URI")

logging.basicConfig(filename='logs/app.log', filemode='a', level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")


if app.debug:
    # Fix werkzeug handler in debug mode
    logging.getLogger('werkzeug').disabled = True

app.register_blueprint(volume_bp)


# with app.app_context():
#     from tasks import update_volumes_collection

# Scheduler for updating db from aws every 10 minutes
CELERYBEAT_SCHEDULE = {
        'update-volumes-collection-every-10-minutes': {
            'task': 'update_volumes_collection',
            'schedule': timedelta(minutes=10)
        }
}

celery.conf.beat_schedule = CELERYBEAT_SCHEDULE


@celery.task(name="update_volumes_collection")
def update_volumes_collection():
    ec2_resource = get_ec2_resource('us-east-1')
    volume_iterator = ec2_resource.volumes.all()
    with app.app_context():
        volumes_on_db = [volume['volume_id'] for volume in db.volumes.find({}, {'_id': 0, 'volume_id': 1})]

        for volume in volume_iterator:
            if volume.id not in volumes_on_db:  # volume not present in the db: add record to db
                vol = {
                    'VolumeId': volume.id,
                    'AvailabilityZone': volume.availability_zone,
                    'CreateTime': volume.create_time,
                    'Encrypted': volume.encrypted,
                    'Size': volume.size,
                    'SnapshotId': volume.snapshot_id,
                    'State': volume.state,
                    'Iops': volume.iops,
                    'VolumeType':volume.volume_type,
                    'MultiAttachEnabled': volume.multi_attach_enabled
                }

                VolumeDbService.create(vol)

        # delete volumes from db that are deleted from aws
        volumes_on_aws = [vol.volume_id for vol in volume_iterator]

        for volume in volumes_on_db:
            if volume not in volumes_on_aws:
                print("volume not on aws: ", volume)
                VolumeDbService.delete(volume)
