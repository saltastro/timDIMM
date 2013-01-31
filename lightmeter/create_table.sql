sqlite> create table light(
   ...> id INTEGER PRIMARY KEY AUTOINCREMENT,
   ...> time timestamp default current_timestamp,
   ...> temperature float,
   ...> rawdata int,
   ...> lux float,
   ...> flag text)
   ...> ;
