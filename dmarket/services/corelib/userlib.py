import os

class UserLib:

    @staticmethod
    def createUser(username):
        ret = os.system('useradd -M -s /usr/sbin/nologin ' + username)
        if ret != 0:
            print('useradd failed: err=' + str(ret), file=sys.stderr)
            return False
        
        os.system('hdfs dfs -mkdir /user')

        cmd = 'hdfs dfs -mkdir /user/' + username
        ret = os.system(cmd)
        if ret != 0:
            print('Fail cmd: ' + cmd, file=sys.stderr)
            os.system('userdel -r ' + username)
            return False

        cmd = 'hdfs dfs -chown {0}:{0} /user/{0}'.format(username)
        ret = os.system(cmd)
        if ret != 0:
            print('Fail cmd: ' + cmd, file=sys.stderr)
            os.system('hdfs dfs -rm -r /user/' + username)
            os.system('userdel -r ' + username)
            return False

        cmd = 'hdfs dfs -chmod -R 750 /user/{0}'.format(username)
        ret = os.system(cmd)
        if ret != 0:
            print('Fail cmd: ' + cmd, file=sys.stderr)
            os.system('hdfs dfs -rm -r /user/' + username)
            os.system('userdel -r ' + username)
            return False

        # cmd = 'hdfs dfs -mkdir /shared/log/{0}'.format(username)
        # ret = os.system(cmd)
        # if ret != 0:
        #     print('Fail cmd: ' + cmd, file=sys.stderr)
        #     os.system('hdfs dfs -rm -r /user/' + username)
        #     os.system('userdel -r ' + username)
        #     return False

        # cmd = 'hdfs dfs -chown {0}:{0} /shared/log/{0}'.format(username)
        # ret = os.system(cmd)
        # if ret != 0:
        #     print('Fail cmd: ' + cmd, file=sys.stderr)
        #     os.system('hdfs dfs -rm -r /shared/log' + username)
        #     os.system('hdfs dfs -rm -r /user/' + username)
        #     os.system('userdel -r ' + username)
        #     return False

        cmd = 'hdfs dfsadmin -refreshUserToGroupsMappings'
        ret = os.system(cmd)
        if ret != 0:
            print('Fail cmd: ' + cmd, file=sys.stderr)
            # os.system('hdfs dfs -rm -r /shared/log' + username)
            os.system('hdfs dfs -rm -r /user/' + username)
            os.system('userdel -r ' + username)
            return False
        
        return True