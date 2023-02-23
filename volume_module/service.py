from .constant import *
import boto3
from utils import parameter_type_error_message
from .model import Volume
from db import db


class VolumeValidationService:
    @staticmethod
    def validate_volume_id(volume_id):
        """Validations for Volume id"""

        if not (isinstance(volume_id, str)):
            raise Exception(VOLUME_NOT_A_STRING)
        elif not (volume_id.startswith("vol-")):
            raise Exception(INVALID_INSTANCE_ID)

    @staticmethod
    def validate_availability_zone(region, zone_name):
        if zone_name is None:
            return "Availability zone must be specified to create a volume."

        ec2_client = boto3.client('ec2', region)

        az_response = ec2_client.describe_availability_zones()

        availability_zones = [zone['ZoneName']
                              for zone in az_response['AvailabilityZones']]

        if zone_name not in availability_zones:
            return f"{zone_name} is not a valid availability zone in region {region}."

    @staticmethod
    def validate_client_token(token):
        if token is None:
            return
        if type(token) is not str:
            return parameter_type_error_message('clientToken', str)

    @staticmethod
    def validate_encrypted(is_encrypted):
        if is_encrypted is None:
            return
        if type(is_encrypted) is not bool:
            return parameter_type_error_message('encrypted', bool)

    @staticmethod
    def validate_iops(iops, volume_type):
        # validations on iop depending on volume type
        if iops is None:
            return
        if not isinstance(iops, int):
            return parameter_type_error_message('Iops', int)

        supported_volumes = ['gp3', 'io1', 'io2']

        if volume_type not in supported_volumes:
            return f"The parameter iops is not supported for {volume_type} volumes."

        if volume_type == 'gp3' and not (3000 <= iops <= 16000):
            return "IOPS must be between 3000 and 16000."
        if volume_type in ['io1', 'io2'] and not (100 <= iops <= 64000):
            return "IOPS must be between 100 and 64000."

    @staticmethod
    def validate_multiattachenabled(is_multiattachenabled, volume_type):
        # validation on multiattachenabled based on volume type
        if is_multiattachenabled is None:
            return None
        if not isinstance(is_multiattachenabled, bool):
            return parameter_type_error_message('multiAttachEnabled', bool)
        if volume_type not in ['io1', 'io2']:
            return "Parameter 'multiAttachEnabled' is supported for io1 and io2 volumes only."

    @staticmethod
    def validate_snapshot_id(snapshot_id):
        if snapshot_id is None:
            return "Snapshot ID is required to create a volume from snapshot."
        if type(snapshot_id) is not str:
            return parameter_type_error_message('SnapshotId', str)
        if not snapshot_id.startswith('snap-'):
            return "Value for parameter 'SnapshotId' is Invalid."

    @staticmethod
    def validate_throughput(throughput):
        if throughput is None:
            return
        if type(throughput) is not int:
            return parameter_type_error_message('throughput', int)
        if not (255 <= throughput <= 1000):
            return "Value for parameter 'throughput' must be in range 255-1000"

    @staticmethod
    def validate_volume_type(volume_type):
        if type(volume_type) is not str:
            return "Value for parameter 'volumeType' must be a string."

        volume_types = ['gp2', 'gp3', 'io1', 'io2', 'st1', 'sc1', 'standard']
        if volume_type not in volume_types:
            return f"Unsupported volume type {volume_type} for volume creation. "

    @staticmethod
    def validate_request_params(params: dict):
        has_invalid_availability_zone = VolumeValidationService.validate_availability_zone(
            params.get('region_name'), params.get('AvailabilityZone'))
        has_invalid_encrypted = VolumeValidationService.validate_encrypted(
            params.get('Encrypted'))
        has_invalid_iops = VolumeValidationService.validate_iops(
            params.get('Iops'), params.get('VolumeType'))
        has_invalid_snapshot_id = VolumeValidationService.validate_snapshot_id(
            params.get('SnapshotId'))
        has_invalid_throughput = VolumeValidationService.validate_throughput(
            params.get('Throughput'))
        has_invalid_multi_attach_enabled = VolumeValidationService.validate_multiattachenabled(
            params.get('MultiAttachEnabled'), params.get('VolumeType'))
        has_invalid_volume_type = VolumeValidationService.validate_volume_type(
            params.get('VolumeType'))
        has_invalid_client_token = VolumeValidationService.validate_client_token(
            params.get('ClientToken'))

        has_invalid_params = (
                has_invalid_availability_zone or
                has_invalid_encrypted or
                has_invalid_iops or
                has_invalid_snapshot_id or
                has_invalid_throughput or
                has_invalid_volume_type or
                has_invalid_multi_attach_enabled or
                has_invalid_volume_type or
                has_invalid_client_token
        )
        return has_invalid_params

    @staticmethod
    def create_request(request_params: dict):
        # Creates a request dictionary object for create snapshot api request
        request = {}

        request_params.pop('region_name')

        for field in request_params.keys():
            if field == 'Tags':
                request['TagSpecifications'] = [
                    {'ResourceType': "volume",
                     'Tags': request_params.get('Tags')}
                ]

            else:
                request[field] = request_params.get(field)

        return request


class VolumeDbService:
    @staticmethod
    def create(volume):
        volume_doc = Volume(
            id=volume['VolumeId'],
            zone=volume['AvailabilityZone'],
            create_time=volume['CreateTime'],
            is_encrypted=volume['Encrypted'],
            size=volume['Size'],
            snapshot_id=volume['SnapshotId'],
            state=volume['State'],
            iops=volume['Iops'],
            volume_type=volume['VolumeType'],
            multi_attach_enabled=volume['MultiAttachEnabled'],
            is_active=1
        )

        db.volumes.insert_one(volume_doc.__dict__)

    @staticmethod
    def list():
        volumes = db.volumes.find({"is_active": 1}, {'_id': 0})
        return volumes

    @staticmethod
    def delete(volume_id):
        db.volumes.update_one({"volume_id": volume_id}, {"$set": {"is_active": 0}})

    @staticmethod
    def hard_delete(volume_id):
        volume = db.volumes.find({"volume_id": volume_id})[0]
        if volume and volume['is_active'] == 0:
            db.volumes.delete_one({"volume_id": volume_id})
