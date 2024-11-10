from src.db.logs import LogsDB

logs = LogsDB().fetch_all_logs()
logs_df = LogsDB().preprocess_logs(logs)

logs_df.to_csv("src/data/logs.csv", index=False)