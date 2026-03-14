from utils.token_detector import detect_token_field


def build_flow(requests):

    flows = []

    for i, req in enumerate(requests):

        payload = req.get("payload", "")

        token = detect_token_field(payload)

        if token and i > 0:

            prev = requests[i - 1]

            flow = {
                "type": "csrf_flow",
                "get_request": prev,
                "post_request": req,
                "token_name": token
            }

            flows.append(flow)

        else:

            flows.append({
                "type": "single",
                "request": req
            })

    return flows