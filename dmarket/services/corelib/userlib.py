import os
import sys

class UserLib:

    @staticmethod
    def createUser(username):
        """
        Create a corresponding user in Linux and create his home directory in
        HDFS. We need to create this, so that we could submit a job with on 
        behalf of the user.

        :param str username: the username to use
        """

        # Create a user with no login shell
        ret = os.system('useradd -M -s /usr/sbin/nologin ' + username)
        if ret != 0:
            print('useradd failed: err=' + str(ret), file=sys.stderr)
            return False
        
        # Create a home directory for the user in HDFS
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

        # Create a home directory for the user in HDFS
        cmd = 'hdfs dfsadmin -refreshUserToGroupsMappings'
        ret = os.system(cmd)
        if ret != 0:
            print('Fail cmd: ' + cmd, file=sys.stderr)
            os.system('hdfs dfs -rm -r /user/' + username)
            os.system('userdel -r ' + username)
            return False
        
        return True