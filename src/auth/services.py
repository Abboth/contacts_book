from user_agents import parse


async def get_user_device(request):
    """
    Detect the type of user device based on User-Agent header.

    :param request: Request containing User-Agent header.
    :type request: Request
    :return: Device type: 'mobile', 'desktop', or 'other'.
    :rtype: str
    """

    user_agent = request.headers.get("user-agent")
    ua = parse(user_agent)
    device_type = "mobile" if ua.is_mobile else "desktop" if ua.is_pc else "other"
    print(ua)

    return device_type