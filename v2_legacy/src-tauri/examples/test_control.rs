use agi_voice_v2_lib::carmaker::CarMakerClient;
use std::io::{self, Write};

#[tokio::main]
async fn main() {
    println!("=== CarMaker Control Test ===\n");

    // Create and connect
    let mut client = CarMakerClient::new("localhost".to_string(), 16660);

    println!("Connecting to CarMaker...");
    match client.connect().await {
        Ok(_) => println!("✓ Connected!\n"),
        Err(e) => {
            eprintln!("✗ Connection failed: {}", e);
            return;
        }
    }

    // Read current state
    println!("Current vehicle state:");
    match client.read_essential_quantities().await {
        Ok(data) => {
            println!("  Speed: {:.2} m/s ({:.1} km/h)", data.car_v.unwrap_or(0.0), data.car_v.unwrap_or(0.0) * 3.6);
            println!("  Gas: {:.2}", data.dm_gas.unwrap_or(0.0));
            println!("  Brake: {:.2}", data.dm_brake.unwrap_or(0.0));
            println!("  Steering: {:.2} rad", data.dm_steer_ang.unwrap_or(0.0));
            println!();
        }
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Test 1: Gas control
    println!("Test 1: Gas pedal control");
    println!("Setting gas to 0.8 for 3 seconds...");
    match client.set_gas(0.8, Some(3000)).await {
        Ok(_) => println!("✓ Gas command sent\n"),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;

    // Test 2: Brake control
    println!("Test 2: Brake control");
    println!("Setting brake to 0.3 for 2 seconds...");
    match client.set_brake(0.3, Some(2000)).await {
        Ok(_) => println!("✓ Brake command sent\n"),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;

    // Test 3: Steering control
    println!("Test 3: Steering control");
    println!("Setting steering angle to 0.2 rad for 2 seconds...");
    match client.set_steer(0.2, Some(2000)).await {
        Ok(_) => println!("✓ Steering command sent\n"),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;

    // Test 4: Target speed
    println!("Test 4: Target speed control");
    println!("Setting target speed to 60 km/h (16.67 m/s)...");
    match client.set_target_speed(16.67).await {
        Ok(_) => println!("✓ Target speed command sent\n"),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Read final state
    println!("Final vehicle state:");
    match client.read_essential_quantities().await {
        Ok(data) => {
            println!("  Speed: {:.2} m/s ({:.1} km/h)", data.car_v.unwrap_or(0.0), data.car_v.unwrap_or(0.0) * 3.6);
            println!("  Gas: {:.2}", data.dm_gas.unwrap_or(0.0));
            println!("  Brake: {:.2}", data.dm_brake.unwrap_or(0.0));
            println!("  Steering: {:.2} rad", data.dm_steer_ang.unwrap_or(0.0));
            println!("  Target Speed: {:.2} m/s ({:.1} km/h)", data.dm_v_trgt.unwrap_or(0.0), data.dm_v_trgt.unwrap_or(0.0) * 3.6);
            println!();
        }
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Interactive mode
    println!("=== Interactive Control Mode ===");
    println!("Commands:");
    println!("  gas <value>     - Set gas pedal (0-1)");
    println!("  brake <value>   - Set brake pedal (0-1)");
    println!("  steer <value>   - Set steering angle (rad)");
    println!("  speed <kmh>     - Set target speed (km/h)");
    println!("  read            - Read current state");
    println!("  cmd <command>   - Execute raw command");
    println!("  quit            - Exit");
    println!();

    loop {
        print!("> ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        let input = input.trim();

        if input.is_empty() {
            continue;
        }

        let parts: Vec<&str> = input.split_whitespace().collect();
        let command = parts[0];

        match command {
            "quit" | "exit" | "q" => break,

            "gas" if parts.len() > 1 => {
                if let Ok(value) = parts[1].parse::<f64>() {
                    match client.set_gas(value, Some(2000)).await {
                        Ok(_) => println!("✓ Gas set to {}", value),
                        Err(e) => println!("✗ Error: {}", e),
                    }
                } else {
                    println!("✗ Invalid value");
                }
            }

            "brake" if parts.len() > 1 => {
                if let Ok(value) = parts[1].parse::<f64>() {
                    match client.set_brake(value, Some(2000)).await {
                        Ok(_) => println!("✓ Brake set to {}", value),
                        Err(e) => println!("✗ Error: {}", e),
                    }
                } else {
                    println!("✗ Invalid value");
                }
            }

            "steer" if parts.len() > 1 => {
                if let Ok(value) = parts[1].parse::<f64>() {
                    match client.set_steer(value, Some(2000)).await {
                        Ok(_) => println!("✓ Steering set to {} rad", value),
                        Err(e) => println!("✗ Error: {}", e),
                    }
                } else {
                    println!("✗ Invalid value");
                }
            }

            "speed" if parts.len() > 1 => {
                if let Ok(kmh) = parts[1].parse::<f64>() {
                    let ms = kmh / 3.6;
                    match client.set_target_speed(ms).await {
                        Ok(_) => println!("✓ Target speed set to {} km/h ({:.2} m/s)", kmh, ms),
                        Err(e) => println!("✗ Error: {}", e),
                    }
                } else {
                    println!("✗ Invalid value");
                }
            }

            "read" | "status" => {
                match client.read_essential_quantities().await {
                    Ok(data) => {
                        println!("  Speed: {:.2} m/s ({:.1} km/h)", data.car_v.unwrap_or(0.0), data.car_v.unwrap_or(0.0) * 3.6);
                        println!("  Gas: {:.2}", data.dm_gas.unwrap_or(0.0));
                        println!("  Brake: {:.2}", data.dm_brake.unwrap_or(0.0));
                        println!("  Steering: {:.2} rad", data.dm_steer_ang.unwrap_or(0.0));
                        println!("  Target Speed: {:.2} m/s ({:.1} km/h)", data.dm_v_trgt.unwrap_or(0.0), data.dm_v_trgt.unwrap_or(0.0) * 3.6);
                    }
                    Err(e) => println!("✗ Error: {}", e),
                }
            }

            "cmd" if parts.len() > 1 => {
                let cmd = parts[1..].join(" ");
                match client.execute_command(&cmd).await {
                    Ok(response) => println!("✓ Response: {}", response),
                    Err(e) => println!("✗ Error: {}", e),
                }
            }

            _ => {
                println!("✗ Unknown command: {}", command);
            }
        }
    }

    client.disconnect();
    println!("\n✓ Disconnected");
}
