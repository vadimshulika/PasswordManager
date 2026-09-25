from flask import Blueprint

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/ping', methods=['GET'])
def ping():
    return {'message': 'Vault API is working!'}, 200