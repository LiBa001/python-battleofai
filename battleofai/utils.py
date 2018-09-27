def generate_get_uri(endpoint: str, **params):
    unpacked_params = [f"{p}={params[p]}" for p in params]

    return endpoint + '?' + '&'.join(unpacked_params)
