use crate::check_key;
use rocket::http::Cookies;
use redis::{Client, Connection, Commands};

#[get("/<full>/<nick>/<score>")]
pub fn score_change(cookies: Cookies, full: String, nick: String, score: i32) -> String{
    if !check_key(cookies){
        return "Bad Key!".to_owned();
    }
    let client = redis::Client::open("redis://127.0.0.1:6379/").unwrap();
    let mut con = client.get_connection().unwrap();

    let key = &format!("{}", full);

    let res: Result<bool, redis::RedisError> = con.exists(key);

    match res{
        Ok(_) => {
            (con.hset(key, "nick", nick) as Result<bool, redis::RedisError>).unwrap();
            (con.hincr(key, "score", score) as Result<bool, redis::RedisError>).unwrap();
            "SUCC".to_owned()
            },
        Err(e) => {
            format!("ERR: {}", e.category())
        }
    }
}

#[get("/<full>?<nick>")]
pub fn get_score(cookies: Cookies, full: String, nick: Option<String>) -> String{
    if !check_key(cookies){
        return "Bad Key!".to_owned();
    }
    let client = redis::Client::open("redis://127.0.0.1:6379/").unwrap();
    let mut con = client.get_connection().unwrap();

    let key = &format!("{}", full);

    let res: Result<bool, redis::RedisError> = con.exists(key);

    match res{
        Ok(_) => {
            if let Some(n) = nick{
                (con.hset(key, "nick", &n) as Result<bool, redis::RedisError>).unwrap();
                println!("{}",&n);
            }
            let name = match (con.hget(key, "nick") as Result<String, redis::RedisError>){
                Ok(s) => s,
                Err(e) => return format!("{} has no points!", full)
            };
            let score = (con.hget(key, "score") as Result<i32, redis::RedisError>).unwrap();
            format!("{} has {} points!", name, score)
            },
        Err(e) => {
            "ERR".to_owned()
        }
    }
}
