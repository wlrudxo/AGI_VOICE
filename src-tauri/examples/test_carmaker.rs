use agi_voice_v2_lib::carmaker::CarMakerClient;

#[tokio::main]
async fn main() {
    println!("=== CarMaker TCP Client Test ===\n");

    // Create client
    let mut client = CarMakerClient::new("localhost".to_string(), 16660);

    // Test connection
    println!("Connecting to CarMaker at localhost:16660...");
    match client.connect().await {
        Ok(_) => println!("✓ Connected successfully!\n"),
        Err(e) => {
            eprintln!("✗ Connection failed: {}\n", e);
            eprintln!("Make sure CarMaker is running with APO enabled on port 16660");
            return;
        }
    }

    // Test 1: Read single value (Car.v - vehicle velocity)
    println!("Test 1: Reading vehicle speed (Car.v)...");
    match client.read_value("Car.v").await {
        Ok(Some(speed)) => {
            let speed_kmh = speed * 3.6;
            println!("✓ Speed: {:.2} m/s ({:.1} km/h)\n", speed, speed_kmh);
        }
        Ok(None) => println!("✓ Speed: No data\n"),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Test 2: Read gas pedal
    println!("Test 2: Reading gas pedal (DM.Gas)...");
    match client.read_value("DM.Gas").await {
        Ok(Some(gas)) => println!("✓ Gas pedal: {:.2}\n", gas),
        Ok(None) => println!("✓ Gas pedal: No data\n"),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Test 3: Set gas pedal
    println!("Test 3: Setting gas pedal to 0.5 for 2 seconds...");
    match client.set_gas(0.5, Some(2000)).await {
        Ok(response) => println!("✓ Command executed: {}\n", response),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Wait a bit
    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;

    // Test 4: Read all essential quantities
    println!("Test 4: Reading all essential quantities...");
    match client.read_essential_quantities().await {
        Ok(data) => {
            println!("✓ Telemetry data received:");
            if let Some(time) = data.time {
                println!("  - Time: {:.2} s", time);
            }
            if let Some(speed) = data.car_v {
                println!("  - Speed: {:.2} m/s ({:.1} km/h)", speed, speed * 3.6);
            }
            if let Some(gas) = data.dm_gas {
                println!("  - Gas: {:.2}", gas);
            }
            if let Some(brake) = data.dm_brake {
                println!("  - Brake: {:.2}", brake);
            }
            if let Some(steer) = data.dm_steer_ang {
                println!("  - Steering: {:.2} rad", steer);
            }
            if let Some(s_road) = data.vhcl_s_road {
                println!("  - Road position (s): {:.2} m", s_road);
            }
            if let Some(t_road) = data.vhcl_t_road {
                println!("  - Lateral position (t): {:.2} m", t_road);
            }
            println!("  - Total quantities read: {}", data.raw_data.len());
            println!();
        }
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Test 5: Raw command execution
    println!("Test 5: Executing raw command (DVARead Time)...");
    match client.execute_command("DVARead Time").await {
        Ok(response) => println!("✓ Response: {}\n", response),
        Err(e) => println!("✗ Error: {}\n", e),
    }

    // Test 6: Start simulation (optional - uncomment if needed)
    // println!("Test 6: Starting simulation...");
    // match client.start_sim().await {
    //     Ok(response) => println!("✓ Response: {}\n", response),
    //     Err(e) => println!("✗ Error: {}\n", e),
    // }

    // Disconnect
    println!("Disconnecting...");
    client.disconnect();
    println!("✓ Disconnected\n");

    println!("=== Test completed ===");
}
