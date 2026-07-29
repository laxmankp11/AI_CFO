<?php

require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';

$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

use App\Models\Tenant;
use App\Models\User;
use App\Models\Customer;
use App\Models\Invoice;
use App\Models\Payment;
use Illuminate\Support\Str;
use Stancl\Tenancy\Facades\Tenancy;

// Find demouser@gmail.com
$user = User::where('email', 'demouser@gmail.com')->first();
if (!$user) {
    echo "Demo user not found!\n";
    exit;
}

$tenant = Tenant::where('id', 'demo')->first();
if (!$tenant) {
    $tenant = Tenant::first();
}

if (!$tenant) {
    echo "No tenant found!\n";
    exit;
}

echo "Initializing tenancy for: " . $tenant->id . "\n";
Tenancy::initialize($tenant);

echo "Adding test data...\n";

// Add some customers
$c1 = Customer::firstOrCreate(['email' => 'client1@example.com'], ['id' => (string) Str::uuid(), 'name' => 'Tech Corp', 'phone' => '1234567890']);
$c2 = Customer::firstOrCreate(['email' => 'client2@example.com'], ['id' => (string) Str::uuid(), 'name' => 'Acme Widgets', 'phone' => '0987654321']);
$c3 = Customer::firstOrCreate(['email' => 'client3@example.com'], ['id' => (string) Str::uuid(), 'name' => 'Global Services', 'phone' => '5555555555']);

// Add Invoices
$inv1 = Invoice::create([
    'id' => (string) Str::uuid(),
    'customer_id' => $c1->id,
    'invoice_number' => 'INV-' . mt_rand(10000, 99999),
    'description' => 'Website Redesign',
    'total_amount' => 45000.00,
    'issue_date' => date('Y-m-d', strtotime('-5 days')),
    'due_date' => date('Y-m-d', strtotime('+10 days')),
    'status' => 'Paid'
]);

$inv2 = Invoice::create([
    'id' => (string) Str::uuid(),
    'customer_id' => $c2->id,
    'invoice_number' => 'INV-' . mt_rand(10000, 99999),
    'description' => 'Server Maintenance',
    'total_amount' => 12500.00,
    'issue_date' => date('Y-m-d', strtotime('-15 days')),
    'due_date' => date('Y-m-d', strtotime('-2 days')),
    'status' => 'Overdue'
]);

$inv3 = Invoice::create([
    'id' => (string) Str::uuid(),
    'customer_id' => $c3->id,
    'invoice_number' => 'INV-' . mt_rand(10000, 99999),
    'description' => 'Monthly Retainer',
    'total_amount' => 20000.00,
    'issue_date' => date('Y-m-d'),
    'due_date' => date('Y-m-d', strtotime('+30 days')),
    'status' => 'Draft'
]);

$inv4 = Invoice::create([
    'id' => (string) Str::uuid(),
    'customer_id' => $c1->id,
    'invoice_number' => 'INV-' . mt_rand(10000, 99999),
    'description' => 'SEO Optimization',
    'total_amount' => 18000.00,
    'issue_date' => date('Y-m-d', strtotime('-2 days')),
    'due_date' => date('Y-m-d', strtotime('+15 days')),
    'status' => 'Issued'
]);

// Add Payments for Paid invoice
Payment::create([
    'id' => (string) Str::uuid(),
    'invoice_id' => $inv1->id,
    'amount' => 45000.00,
    'payment_date' => date('Y-m-d', strtotime('-1 days')),
    'method' => 'Bank Transfer'
]);

// Partial payment for issued invoice
Payment::create([
    'id' => (string) Str::uuid(),
    'invoice_id' => $inv4->id,
    'amount' => 5000.00,
    'payment_date' => date('Y-m-d'),
    'method' => 'Cash'
]);

echo "Done seeding real data!\n";
