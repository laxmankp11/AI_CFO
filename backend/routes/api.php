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
    Route::put('/tenants/{id}/modules', [TenantController::class, 'updateModules']);
    Route::get('/system-settings', [SettingsController::class, 'index']);
    Route::post('/system-settings', [SettingsController::class, 'update']);
    Route::get('/global-tax-rules', [GlobalTaxRuleController::class, 'index']);
    Route::post('/global-tax-rules', [GlobalTaxRuleController::class, 'store']);
});

// Business Owner Route: Create Supplier (Scoped by X-Tenant-ID header)
Route::middleware([\App\Http\Middleware\InitializeTenancyByHeader::class])->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index']);
    
    // Core master data
    Route::get('/settings', [SettingsController::class, 'index']);
    Route::post('/settings', [SettingsController::class, 'update']);
    Route::get('/accounts', [SettingsController::class, 'accounts']);
    
    // Tax Engine
    Route::get('/tenant-tax-settings', [TenantTaxSettingController::class, 'index']);
    Route::post('/tenant-tax-settings', [TenantTaxSettingController::class, 'update']);
    
    Route::get('/customers', [CustomerController::class, 'index']);
    Route::post('/customers', [CustomerController::class, 'store']);
    Route::get('/suppliers', [SupplierController::class, 'index']);
    Route::post('/suppliers', [SupplierController::class, 'store']);
    
    Route::get('/journal-entries', [JournalEntryController::class, 'index']);
    Route::post('/journal-entries', [JournalEntryController::class, 'store']);
    
    // Invoices (Sales)
    Route::get('/invoices', [InvoiceController::class, 'index']);
    Route::post('/invoices', [InvoiceController::class, 'store']);
    Route::post('/invoices/ai-create', [InvoiceController::class, 'aiCreate']); // Atomic AI Route
    Route::post('/invoices/{id}/payments', [PaymentController::class, 'store']);
    
    // Purchase Bills (Expenses)
    Route::get('/purchase-bills', [PurchaseBillController::class, 'index']);
    Route::post('/purchase-bills/ai-create', [PurchaseBillController::class, 'aiCreate']);
    
    // Reports
    Route::get('/reports/profit-and-loss', [\App\Http\Controllers\ReportController::class, 'profitAndLoss']);
});
