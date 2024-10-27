def simple_middleware(get_response):

    def middleware(request):
        response = get_response(request)

        response["Access-Control-Allow-Origin"]="http://localhost:3000/"
        response["Access-Control-Allow-Credentials"]= "true"
        response["Access-Control-Allow-Methods"]="GET,HEAD,OPTIONS,POST,PUT"
        response["Access-Control-Allow-Headers"]="Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"

        return response

    return middleware