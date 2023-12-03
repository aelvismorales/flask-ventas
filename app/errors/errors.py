from flask import jsonify


def handle_bad_request(error):
    """
    Error handler for BadRequest (400) errors.
    Se lanza cuando la solicitud HTTP no se puede cumplir debido a un error del cliente,
    como una solicitud mal formada. Corresponde al código de estado HTTP 400.
    """

    return jsonify({"mensaje": str(error), "http_code": 400}), 400

def handle_conflict(error):
    """
    Error handler for Conflict (409) errors.
    Se lanza cuando la solicitud no se puede completar debido a un conflicto 
    con el estado actual del recurso. 
    Corresponde al código de estado HTTP 409.
    """
    return jsonify({"mensaje": str(error), "http_code": 409}), 409

def handle_forbidden(error):
    """
    Error handler for Forbidden (403) errors.
    Se lanza cuando el cliente no tiene permisos para acceder a un recurso.
    Corresponde al código de estado HTTP 403.
    """
    return jsonify({"mensaje": str(error), "http_code": 403}), 403

def handle_not_found(error):
    """
    Error handler for NotFound (404) errors.
    Se lanza cuando el recurso solicitado no se puede encontrar. 
    Corresponde al código de estado HTTP 404.
    """
    return jsonify({"mensaje": str(error), "http_code": 404}), 404

def handle_unauthorized(error):
    """
    Error handler for Unauthorized (401) errors.
    Se lanza cuando se requiere autenticación para acceder a un recurso. 
    Corresponde al código de estado HTTP 401.
    """
    return jsonify({"mensaje": str(error), "http_code": 401}), 401

def handle_method_not_allowed(error):
    """
    Error handler for MethodNotAllowed (405) errors.
    Se lanza cuando se utiliza un método HTTP que no está permitido para el recurso solicitado. 
    Corresponde al código de estado HTTP 405.
    """
    return jsonify({"mensaje": str(error), "http_code": 405}), 405

def handle_internal_server_error(error):
    """
    Error handler for InternalServerError (500) errors.
    Se lanza cuando ocurre un error en el servidor. Corresponde al código de estado HTTP 500.
    """
    return jsonify({"mensaje": str(error), "http_code": 500}), 500
