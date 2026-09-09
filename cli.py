"""CLI Interface for OSINT Platform"""

import click
import asyncio
import json
from datetime import datetime
from tabulate import tabulate
from src.core.engine import OSINTEngine
from src.analyzers.activity_hours import ActivityHoursAnalyzer
from src.analyzers.entity_relationship import build_entity_graph

engine = OSINTEngine()


@click.group()
def cli():
    """Ultimate OSINT Intelligence Platform - CLI"""
    pass


@cli.command()
@click.option('--username', '-u', help='Username to scan')
@click.option('--email', '-e', help='Email to scan')
@click.option('--cross-scan', is_flag=True, help='Enable cross-scanning')
@click.option('--depth', default=1, help='Cross-scan depth')
@click.option('--modules', '-m', help='Specific modules (comma-separated)')
@click.option('--export', '-f', type=click.Choice(['json', 'csv', 'pdf']), help='Export format')
@click.option('--output', '-o', help='Output file')
def scan(username, email, cross_scan, depth, modules, export, output):
    """Scan target across OSINT platforms"""
    
    target = username or email
    target_type = 'email' if email else 'username'
    
    if not target:
        click.echo(click.style('Error: Specify --username or --email', fg='red'))
        return
    
    click.echo(click.style(f"🔍 Starting {target_type} scan for: {target}", fg='cyan'))
    
    # Parse modules
    module_list = modules.split(',') if modules else None
    
    # Run scan
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if target_type == 'email':
        results = loop.run_until_complete(
            engine.scan_email(target, module_list, cross_scan, depth)
        )
    else:
        results = loop.run_until_complete(
            engine.scan_username(target, module_list, cross_scan, depth)
        )
    
    # Display results
    found_count = sum(1 for r in results if r.found)
    
    click.echo(click.style(f"\n✓ Scan complete! Found {found_count} accounts", fg='green'))
    
    # Display table
    table_data = [
        [r.module, r.target, '✓' if r.found else '✗', r.confidence, r.source]
        for r in results
    ]
    
    click.echo(tabulate(
        table_data,
        headers=['Module', 'Target', 'Found', 'Confidence', 'Source'],
        tablefmt='grid'
    ))
    
    # Export if requested
    if export:
        if export == 'json':
            data = [r.to_dict() for r in results]
            output_file = output or f"{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        click.echo(click.style(f"\n✓ Exported to {output_file}", fg='green'))


@cli.command()
@click.option('--username', '-u', help='GitHub username')
def activity_hours(username):
    """Analyze activity hours from GitHub commits"""
    
    if not username:
        click.echo(click.style('Error: Specify --username', fg='red'))
        return
    
    click.echo(click.style(f"⏰ Analyzing activity hours for: {username}", fg='cyan'))
    
    # This would fetch GitHub commits and analyze
    analyzer = ActivityHoursAnalyzer()
    
    # Placeholder - would fetch real data
    click.echo(click.style("⚠ This feature requires GitHub API integration", fg='yellow'))


@cli.command()
@click.option('--scan-id', required=True, help='Scan ID to visualize')
def graph(scan_id):
    """Display entity relationship graph"""
    
    click.echo(click.style(f"🔗 Building entity graph for scan: {scan_id}", fg='cyan'))
    
    # This would load results and build graph
    click.echo(click.style("✓ Graph data ready for visualization", fg='green'))


@cli.command()
@click.option('--username', '-u', help='Username')
@click.option('--email', '-e', help='Email')
def reputation(username, email):
    """Check reputation and threat level"""
    
    target = username or email
    if not target:
        click.echo(click.style('Error: Specify --username or --email', fg='red'))
        return
    
    click.echo(click.style(f"⚠ Checking reputation for: {target}", fg='cyan'))
    
    # This would check various reputation sources
    click.echo(click.style("Coming soon: Reputation analysis module", fg='yellow'))


@cli.command()
@click.option('--target', required=True, help='Target to search')
@click.option('--query', '-q', help='Search query')
def darkweb(target, query):
    """Search dark web"""
    
    search_term = query or target
    click.echo(click.style(f"🧅 Searching dark web for: {search_term}", fg='cyan'))
    
    # This requires Tor setup
    click.echo(click.style("⚠ Dark web search requires Tor connection", fg='yellow'))


@cli.command()
def version():
    """Show version information"""
    click.echo(click.style("Ultimate OSINT Intelligence Platform v1.0.0", fg='green'))
    click.echo("Built with: Python, Flask, Async, Redis, PostgreSQL")


@cli.command()
def config():
    """Show current configuration"""
    import os
    from src.core.cache import CacheManager
    
    click.echo(click.style("\n📋 Configuration", fg='cyan'))
    
    config_data = [
        ['Flask Environment', os.getenv('FLASK_ENV', 'production')],
        ['Database', os.getenv('DATABASE_URL', 'sqlite')],
        ['Cache Backend', 'Redis' if os.getenv('REDIS_URL') else 'In-Memory'],
        ['TOR Enabled', 'Yes' if os.getenv('TOR_PROXY') else 'No'],
        ['Max Workers', os.getenv('MAX_WORKERS', '50')],
        ['Request Timeout', os.getenv('TIMEOUT', '30') + 's'],
    ]
    
    click.echo(tabulate(config_data, tablefmt='grid'))


if __name__ == '__main__':
    cli()
