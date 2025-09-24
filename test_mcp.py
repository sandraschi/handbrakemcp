#!/usr/bin/env python3
"""Test script for HandBrake MCP server."""
import json
import subprocess
import time

print('Testing HandBrake MCP server stdio mode...')

proc = subprocess.Popen(
    ['python', '-m', 'handbrake_mcp.main'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8'
)

try:
    time.sleep(2)

    init_request = {
        'jsonrpc': '2.0',
        'id': 0,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {
                'name': 'claude-ai',
                'version': '0.1.0'
            }
        }
    }

    proc.stdin.write(json.dumps(init_request) + '\n')
    proc.stdin.flush()

    response_line = proc.stdout.readline().strip()

    if response_line:
        try:
            response = json.loads(response_line)
            print('✅ SUCCESS: HandBrake MCP server initialized!')
            server_info = response.get('result', {}).get('serverInfo', {})
            print(f'Server: {server_info.get("name", "unknown")}')
            print(f'Version: {server_info.get("version", "unknown")}')
            print(f'Protocol: {response.get("result", {}).get("protocolVersion", "unknown")}')

            # Test tools/list
            tools_request = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/list',
                'params': {}
            }

            proc.stdin.write(json.dumps(tools_request) + '\n')
            proc.stdin.flush()

            tools_response = proc.stdout.readline().strip()
            if tools_response:
                tools_data = json.loads(tools_response)
                tools_count = len(tools_data.get('result', {}).get('tools', []))
                print(f'Tools available: {tools_count}')

        except json.JSONDecodeError:
            print('❌ ERROR: Invalid JSON response')
            print(f'Raw: {response_line[:200]}...')
    else:
        print('❌ ERROR: No response from server')
        error_output = proc.stderr.read()
        if error_output.strip():
            print(f'Stderr: {error_output[:500]}...')

except Exception as e:
    print(f'❌ Exception: {e}')

finally:
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except:
        pass
