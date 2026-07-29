<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\TenantController;
use App\Http\Controllers\SupplierController;
use App\Http\Controllers\JournalEntryController;
use App\Http\Controllers\SettingsController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\CustomerController;
use App\Http\Controllers\InvoiceController;
use App\Http\Controllers\PaymentController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\PurchaseBillController;
use App\Http\Controllers\GlobalTaxRuleController;
use App\Http\Controllers\TenantTaxSettingController;

Route::post('/login', [AuthController::class, 'login']);

Route::middleware('auth:sanctum')->group(function () {
    Route::get('/user', function (Request $request) {
        return $request->user();
    });
    
    // Super Admin Routes
    Route::post('/tenants', [TenantController::class, 'store']);
    Route::get('/tenants', [TenantController::class, 'index']);
    Route::get('/settings', [SettingsController::class, 'index']);
    Route::post('/settings', [SettingsController::class, 'store']);
    Route::get('/global-tax-rules', [GlobalTaxRuleController::class, 'index']);
    Route::post('/global-tax-rules', [GlobalTaxRuleController::class, 'store']);
});

// Business Owner Route: Create Supplier (Scoped by X-Tenant-ID header)
Route::middleware(\App\Http\Middleware\InitializeTenancyByHeader::class)->group(function () {
    Route::post('/suppliers', [SupplierController::class, 'store']);
    Route::post('/journal-entries', [JournalEntryController::class, 'store']);
    Route::get('/journal-entries', [JournalEntryController::class, 'index']);
    Route::get('/purchase-bills', [PurchaseBillController::class, 'index']);
    
    Route::get('/tenant-tax-settings', [TenantTaxSettingController::class, 'show']);
    Route::post('/tenant-tax-settings', [TenantTaxSettingController::class, 'update']);

    Route::get('/accounts', function () {
        return response()->json([
            'data' => \Illuminate\Support\Facades\DB::table('accounts')->get()
        ]);
    });

    Route::get('/suppliers', function () {
        return response()->json([
            'data' => \Illuminate\Support\Facades\DB::table('suppliers')->get()
        ]);
    });

    // Dashboard
    Route::get('/dashboard', [DashboardController::class, 'index']);

    // Customers
    Route::get('/customers', [CustomerController::class, 'index']);
    Route::post('/customers', [CustomerController::class, 'store']);

    // Invoices
    Route::get('/invoices', [InvoiceController::class, 'index']);
    Route::post('/invoices', [InvoiceController::class, 'store']);
    Route::post('/invoices/ai-create', [InvoiceController::class, 'aiCreate']);
    Route::post('/invoices/{invoiceId}/payments', [PaymentController::class, 'store']);
});
