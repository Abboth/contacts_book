from user_agents import parse


async def get_user_device(request):
    user_agent = request.headers.get("user-agent")
    ua = parse(user_agent)
    device_type = "mobile" if ua.is_mobile else "desktop" if ua.is_pc else "other"
    print(ua)

    return device_type