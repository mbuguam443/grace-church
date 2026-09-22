<?php
// Grace Church Munyaka - Management Script
// Access this file via browser (file-based deployment, no SSH needed)

// Find the app's virtualenv Python (created by cPanel "Setup Python App")
function gc_python() {
    $candidates = [
        __DIR__ . '/venv/bin/python',
        __DIR__ . '/../venv/bin/python',
        getenv('VIRTUAL_ENV') ? getenv('VIRTUAL_ENV') . '/bin/python' : '',
        'python3',
        'python',
    ];
    foreach ($candidates as $bin) {
        if ($bin && (is_file($bin) || trim($bin) === 'python3' || trim($bin) === 'python')) {
            return $bin;
        }
    }
    return 'python3';
}
$PY = gc_python();

if (isset($_GET['action'])) {
    $action = $_GET['action'];
    $output = [];
    $return_var = 0;
    
    switch ($action) {
        case 'migrate':
            exec(escapeshellarg($PY) . ' manage.py migrate --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Migrations';
            break;
        case 'collectstatic':
            exec(escapeshellarg($PY) . ' manage.py collectstatic --noinput --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Collect Static Files';
            break;
        case 'seed':
            exec(escapeshellarg($PY) . ' manage.py seed_data --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Seed Demo Data';
            break;
        case 'setup_all':
            exec(escapeshellarg($PY) . ' manage.py migrate --settings=fbms.settings_production 2>&1', $output, $return_var);
            exec(escapeshellarg($PY) . ' manage.py collectstatic --noinput --settings=fbms.settings_production 2>&1', $output, $return_var);
            exec(escapeshellarg($PY) . ' manage.py seed_data --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Full Setup';
            break;
        case 'setup_media':
            $media = [];
            exec(escapeshellarg($PY) . ' setup_media.py 2>&1', $media, $return_var);
            $output = $media;
            exec(escapeshellarg($PY) . ' link_media.py 2>&1', $media, $return_var);
            $output = array_merge($output, $media);
            $title = 'Media Setup';
            break;
        default:
            $title = 'Unknown Action';
            $output = ['Invalid action'];
            $return_var = 1;
    }
    
    $status = ($return_var === 0) ? 'SUCCESS' : 'ERROR';
    $status_color = ($return_var === 0) ? 'green' : 'red';
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Grace Church Munyaka - Management</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #A8704A; }
        .btn { display: inline-block; padding: 10px 20px; margin: 10px; background: #A8704A; color: white; text-decoration: none; border-radius: 5px; }
        .btn:hover { background: #7E4F2D; }
        .output { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 20px; white-space: pre-wrap; font-family: monospace; }
        .status { color: <?php echo $status_color; ?>; font-weight: bold; }
    </style>
</head>
<body>
        <h1>Grace Church Munyaka Management</h1>
    <p>File-based cPanel setup — click a button (no SSH/terminal needed):</p>
    
    <a class="btn" href="?action=migrate">Run Migrations</a>
    <a class="btn" href="?action=collectstatic">Collect Static Files</a>
    <a class="btn" href="?action=seed">Seed Demo Data</a>
    <a class="btn" href="?action=setup_media">Link Media Files</a>
    <a class="btn" href="?action=setup_all">Run All Setup</a>
    
    <?php if (isset($title)): ?>
    <h2 class="status"><?php echo $title; ?>: <?php echo $status; ?></h2>
    <div class="output"><?php echo implode("\n", $output); ?></div>
    <?php endif; ?>
</body>
</html>
