def get_token():
    ret = open('token.tf').readline()

    if '\n' in ret:
        return ret[:len(ret)-2]
    else:
        return ret
