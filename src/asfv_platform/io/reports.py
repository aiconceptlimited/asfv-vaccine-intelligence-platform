#!/usr/bin/env python3
"""
Report Generation Utilities
"""

from datetime import datetime

def create_download_report(genomes, results, verification, output_dir, email):
    """Create download report dictionary"""
    valid_genomes = [g for g in genomes if g.get('is_valid', True)]
    successful = sum(1 for r in results if r.get('success', False))
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_genomes': len(genomes),
        'valid_genomes': len(valid_genomes),
        'invalid_genomes': len(genomes) - len(valid_genomes),
        'successful_downloads': successful,
        'failed_downloads': len(valid_genomes) - successful,
        'all_verified': verification.get('all_valid', False),
        'email_used': email,
        'output_dir': str(output_dir),
        'downloads': results,
        'verification': verification
    }
