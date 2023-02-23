from .constant import *
from flask import request, jsonify
from .service import VolumeValidationService, VolumeDbService
from botocore.exceptions import ClientError
import logging
from http import HTTPStatus
from utils import get_ec2_client, parse_json


# Creating Logger object
logger = logging.getLogger("volume")


def create_volume():
    """creates a volume from an existing snapshot"""

    params = request.get_json()

    # validate request parameters
    has_invalid_params = VolumeValidationService.validate_request_params(params)
    try:
        if has_invalid_params is not None:
            raise Exception(has_invalid_params)

        volume_params = VolumeValidationService.create_request(dict(params))
        ec2_client = get_ec2_client(params['region_name'])

        logger.info(f"New volume is being created.")
        volume = ec2_client.create_volume(**volume_params)

        # waits until volume is created
        waiter = ec2_client.get_waiter('volume_available')

        waiter.wait(Filters=[
            {
                'Name': 'volume-id',
                'Values': [
                    volume['VolumeId']
                ]
            },
        ])

        logger.info(f"Volume: {volume['VolumeId']} is created successfully.")

        VolumeDbService.create(volume)

    except ClientError as e:
        logger.info(
            f"Code:{e.response['Error']['Code']} Message:{e.response['Error']['Message']}")

        return jsonify({"error": e.response['Error']['Message']}), HTTPStatus.BAD_REQUEST

    except Exception as e:
        logger.info(str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify(NEW_VOLUME_CREATED), HTTPStatus.CREATED


def list_volumes():
    """Lists all encrypted and unencrypted ebs volumes"""
    # region = request.args.get('region')

    try:
        logger.info(
            f"Fetching all volumes")

        # Fetching volume records from the db
        volumes = list(VolumeDbService.list())

        if not volumes:
            return jsonify({"message": NO_VOLUMES_IN_REGION}), HTTPStatus.OK

    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({"volumes": parse_json(volumes)})


def delete_volume():
    """Deletes volume"""

    params = request.get_json()

    try:
        ec2_client = get_ec2_client(params['region'])

        # deleting volume
        logger.info(f"Volume {params['volume_id']} is being deleted.")
        response = ec2_client.delete_volume(VolumeId=params["volume_id"])

        # waits until volume is deleted
        waiter = ec2_client.get_waiter('volume_deleted')

        waiter.wait(VolumeIds=[
            params["volume_id"],
        ])

        VolumeDbService.delete(params["volume_id"])

    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        return jsonify({"error":e.response['Error']['Message']}), HTTPStatus.BAD_REQUEST

    except Exception as e:
        logger.info(str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify(VOLUME_DELETED_SUCCESSFULLY), HTTPStatus.OK


def delete_volume_from_db():
    params = request.get_json()

    try:
        VolumeDbService.hard_delete(params["volume_id"])
    except Exception as e:
        logger.info(str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({"message": "Volume removed from db successfully."}), HTTPStatus.OK


