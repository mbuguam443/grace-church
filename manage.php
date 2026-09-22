<?php
// Grace Church Munyaka - Management Script
// Access this file via browser to run management commands

if (isset($_GET['action'])) {
    $action = $_GET['action'];
    $output = [];
    $return_var = 0;
    
    switch ($action) {
        case 'migrate':
            exec('python manage.py migrate --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Migrations';
            break;
        case 'collectstatic':
            exec('python manage.py collectstatic --noinput --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Collect Static Files';
            break;
        case 'seed':
            exec('python manage.py seed_data --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Seed Demo Data';
            break;
        case 'setup_all':
            exec('python manage.py migrate --settings=fbms.settings_production 2>&1', $output, $return_var);
            exec('python manage.py collectstatic --noinput --settings=fbms.settings_production 2>&1', $output, $return_var);
            exec('python manage.py seed_data --settings=fbms.settings_production 2>&1', $output, $return_var);
            $title = 'Full Setup';
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
    <p>Click the buttons below to run management commands:</p>
    
    <a class="btn" href="?action=migrate">Run Migrations</a>
    <a class="btn" href="?action=collectstatic">Collect Static Files</a>
    <a class="btn" href="?action=seed">Seed Demo Data</a>
    <a class="btn" href="?action=setup_all">Run All Setup</a>
    
    <?php if (isset($title)): ?>
    <h2 class="status"><?php echo $title; ?>: <?php echo $status; ?></h2>
    <div class="output"><?php echo implode("\n", $output); ?></div>
    <?php endif; ?>
</body>
</html>
