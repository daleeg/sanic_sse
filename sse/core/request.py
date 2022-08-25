import uuid

REAL_IP_HEADER_LOWER = "X-Real-IP".lower()
FORWARDED_FOR_HEADER_LOWER = "X-Forwarded-For".lower()


def get_group_id(request):
    def get_real_ip():
        return request.headers.get(REAL_IP_HEADER_LOWER)

    def get_forwarded_for_ip():
        forwarded_for = request.headers.get(FORWARDED_FOR_HEADER_LOWER, "")
        if " " in forwarded_for:
            forwarded_for = forwarded_for.split("")[0]
        if "," in forwarded_for:
            forwarded_for = forwarded_for.split(",")[0]
        return forwarded_for

    return request.remote_addr or get_real_ip() or get_forwarded_for_ip() or request.ip or uuid.uuid4().hex[:12]
