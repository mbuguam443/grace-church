<?php
// Grace Church Munyaka - Web Setup Script
// Upload this file to your cPanel and access via browser
// URL: http://yourdomain.com/setup.php

header('Content-Type: text/html; charset=utf-8');

$action = isset($_GET['action']) ? $_GET['action'] : '';
$output = '';
$status = '';

if ($action) {
    $commands = [
        'migrate' => 'python manage.py migrate --settings=fbms.settings_production 2>&1',
        'collectstatic' => 'python manage.py collectstatic --noinput --settings=fbms.settings_production 2>&1',
        'seed' => 'python manage.py seed_data --settings=fbms.settings_production 2>&1',
    ];
    
    if ($action === 'setup_all') {
        $cmd = $commands['migrate'] . ' && ' . $commands['collectstatic'] . ' && ' . $commands['seed'];
    } elseif (isset($commands[$action])) {
        $cmd = $commands[$action];
    } else {
        $cmd = '';
    }
    
    if ($cmd) {
        $result = shell_exec($cmd);
        $output = $result ?: 'Command executed (no output)';
        $status = 'SUCCESS';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Grace Church Munyaka - Setup</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f2f5; padding: 40px 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #4E3A2C; text-align: center; margin-bottom: 10px; }
        p.subtitle { text-align: center; color: #6c757d; margin-bottom: 30px; }
        .card { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .btn { display: block; width: 100%; padding: 15px 20px; margin: 10px 0; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; transition: all 0.3s; }
        .btn-migrate { background: #A8704A; color: white; }
        .btn-static { background: #28a745; color: white; }
        .btn-seed { background: #C9A24B; color: white; }
        .btn-all { background: #B5651D; color: white; font-size: 18px; }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); }
        .output { background: #1e1e1e; color: #0f0; padding: 20px; border-radius: 8px; margin-top: 20px; font-family: monospace; font-size: 13px; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
        .status { text-align: center; padding: 10px; border-radius: 5px; margin-top: 15px; font-weight: 600; }
        .status-success { background: #d4edda; color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Grace Church Munyaka Setup</h1>
        <p class="subtitle">Click the buttons below to setup your website</p>
        
        <div class="card">
            <a class="btn btn-migrate" href="?action=migrate">1. Run Migrations</a>
            <a class="btn btn-static" href="?action=collectstatic">2. Collect Static Files</a>
            <a class="btn btn-seed" href="?action=seed">3. Seed Demo Data</a>
            <a class="btn btn-all" href="?action=setup_all">Run All Setup</a>
        </div>
        
        <?php if ($action): ?>
        <div class="status status-success"><?php echo $status; ?></div>
        <div class="output"><?php echo htmlspecialchars($output); ?></div>
        <?php endif; ?>
    </div>
</body>
</html>
