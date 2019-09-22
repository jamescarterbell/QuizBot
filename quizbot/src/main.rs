#![feature(proc_macro_hygiene, decl_macro)]
#[macro_use] extern crate rocket;
extern crate redis;
mod score;

use rocket::http::Cookies;

const TOKEN: &str = "";


fn main(){
    rocket::ignite().mount("/", routes![score::score_change])
                    .mount("/", routes![score::get_score])
                    .launch();
}

pub fn check_key(cookies: Cookies) -> bool{
    let key = cookies.get("key").map(|value| format!("{}", value));
    
    match key{
        Some(mut k) =>{
            k.replace_range(0..4, "");
            k == TOKEN},
        None => false 
    }
}