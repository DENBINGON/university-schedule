import api

def group_validate(group=""):
    try:
        int(str(group)[:2])
        if group.count("-") == 2:
            _api = api.Api()
            if _api.check_group(group): return True
        else:
            return False
    except:
        return False


