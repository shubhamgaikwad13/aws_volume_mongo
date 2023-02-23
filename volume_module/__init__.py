from flask import Blueprint
from .controller import *

# create Volume Blueprint
volume_bp = Blueprint(
    'volume', __name__, url_prefix='/api/ec2/ebs')

volume_bp.add_url_rule(
    '/create', 'create_ebs_volume', create_volume, methods=['POST'])

volume_bp.add_url_rule(
    '/list', 'list_ebs_volumes', list_volumes, methods=['GET'])

volume_bp.add_url_rule(
    '/delete', 'delete_ebs_volume', delete_volume, methods=['DELETE'])


volume_bp.add_url_rule(
    '/delete_from_db', 'delete_volume_from_db', delete_volume_from_db, methods=['DELETE'])
