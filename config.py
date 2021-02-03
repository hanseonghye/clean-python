db = {
    'user' : 'root',
    'password' : '',
    'host' : 'localhost',
    'port' : 3306,
    'database' : 'miniter'
}

db_url = f"mysql+mysqlconnector://{db['username']}:{db['password']}@{db['host']}{db['port']}/{db['database']}?charset=utf8"