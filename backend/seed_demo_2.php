<?php

require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';

$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

use App\Models\Tenant;
use App\Models\User;
use App\Models\Account;
use App\Models\JournalEntry;
use App\Models\JournalLine;
use Illuminate\Support\Str;
use Stancl\Tenancy\Facades\Tenancy;

$tenant = Tenant::first();

if (!$tenant) {
    echo "No tenant found!\n";
    exit;
}

echo "Initializing tenancy for: " . $tenant->id . "\n";
Tenancy::initialize($tenant);

echo "Seeding accounts and journals...\n";
use Illuminate\Database\Eloquent\Model;
Model::unguard();

// Add default accounts
$cash = Account::firstOrCreate(['code' => '1000'], ['id' => (string) Str::uuid(), 'name' => 'Cash', 'type' => 'Asset']);
$sales = Account::firstOrCreate(['code' => '4000'], ['id' => (string) Str::uuid(), 'name' => 'Sales Revenue', 'type' => 'Revenue']);
$ar = Account::firstOrCreate(['code' => '1100'], ['id' => (string) Str::uuid(), 'name' => 'Accounts Receivable', 'type' => 'Asset']);

// Add Journal Entry for Initial Capital/Cash
$je1 = JournalEntry::create([
    'id' => (string) Str::uuid(),
    'entry_date' => date('Y-m-d', strtotime('-30 days')),
    'narration' => 'Initial Capital'
]);

JournalLine::create([
    'id' => (string) Str::uuid(),
    'journal_entry_id' => $je1->id,
    'account_id' => $cash->id,
    'debit_amount' => 500000.00,
    'credit_amount' => 0
]);

JournalLine::create([
    'id' => (string) Str::uuid(),
    'journal_entry_id' => $je1->id,
    'account_id' => $sales->id,
    'debit_amount' => 0,
    'credit_amount' => 500000.00
]);

// Add another JE for Cash payment from a customer
$je2 = JournalEntry::create([
    'id' => (string) Str::uuid(),
    'entry_date' => date('Y-m-d', strtotime('-2 days')),
    'narration' => 'Customer Payment Received'
]);

JournalLine::create([
    'id' => (string) Str::uuid(),
    'journal_entry_id' => $je2->id,
    'account_id' => $cash->id,
    'debit_amount' => 45000.00,
    'credit_amount' => 0
]);

JournalLine::create([
    'id' => (string) Str::uuid(),
    'journal_entry_id' => $je2->id,
    'account_id' => $ar->id,
    'debit_amount' => 0,
    'credit_amount' => 45000.00
]);


echo "Done seeding journals and accounts!\n";
