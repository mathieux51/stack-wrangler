use actix_cors::Cors;
use actix_web::{middleware, web, App, HttpResponse, HttpServer, Result};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct HealthResponse {
    status: String,
    service: String,
}

#[derive(Serialize, Deserialize)]
struct PredictionRequest {
    data: Vec<f32>,
}

#[derive(Serialize, Deserialize)]
struct PredictionResponse {
    prediction: f32,
    confidence: f32,
}

async fn health_check() -> Result<HttpResponse> {
    let response = HealthResponse {
        status: "healthy".to_string(),
        service: "rust-backend".to_string(),
    };
    Ok(HttpResponse::Ok().json(response))
}

async fn process_data(req: web::Json<PredictionRequest>) -> Result<HttpResponse> {
    let data_sum: f32 = req.data.iter().sum();
    let data_mean = if req.data.is_empty() {
        0.0
    } else {
        data_sum / req.data.len() as f32
    };
    
    let response = PredictionResponse {
        prediction: data_mean,
        confidence: 0.95,
    };
    
    Ok(HttpResponse::Ok().json(response))
}

async fn forward_to_ai(req: web::Json<PredictionRequest>) -> Result<HttpResponse> {
    let client = reqwest::Client::new();
    
    match client
        .post("http://localhost:8001/api/predict")
        .json(&req.into_inner())
        .send()
        .await
    {
        Ok(resp) => {
            match resp.json::<PredictionResponse>().await {
                Ok(prediction) => Ok(HttpResponse::Ok().json(prediction)),
                Err(_) => Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                    "error": "Failed to parse AI service response"
                }))),
            }
        }
        Err(_) => Ok(HttpResponse::ServiceUnavailable().json(serde_json::json!({
            "error": "AI service is not available"
        }))),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));
    
    println!("Starting Rust backend server on http://localhost:8000");
    
    HttpServer::new(|| {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);
        
        App::new()
            .wrap(cors)
            .wrap(middleware::Logger::default())
            .route("/api/health", web::get().to(health_check))
            .route("/api/process", web::post().to(process_data))
            .route("/api/predict", web::post().to(forward_to_ai))
    })
    .bind(("127.0.0.1", 8000))?
    .run()
    .await
}