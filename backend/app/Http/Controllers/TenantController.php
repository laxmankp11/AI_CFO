<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Tenant;

class TenantController extends Controller
{
    public function index()
    {
        $tenants = Tenant::all();
        
        // Fetch the user count for each tenant
        $tenantData = $tenants->map(function ($tenant) {
            $userCount = \Illuminate\Support\Facades\DB::table('user_tenants')
                ->where('tenant_id', $tenant->id)
                ->count();
                
            // Fetch the primary owner
            $ownerPivot = \Illuminate\Support\Facades\DB::table('user_tenants')
                ->where('tenant_id', $tenant->id)
                ->where('role', 'Business Owner')
                ->first();
                
            $ownerEmail = 'N/A';
            if ($ownerPivot) {
                $ownerUser = \Illuminate\Support\Facades\DB::table('users')->where('id', $ownerPivot->user_id)->first();
                if ($ownerUser) {
                    $ownerEmail = $ownerUser->email;
                }
            }
                
            return [
                'id' => $tenant->id,
                'business_name' => $tenant->business_name,
                'owner_email' => $ownerEmail,
                'pan' => $tenant->pan,
                'users' => $userCount,
                'status' => 'Active' // Hardcoded for now
            ];
        });

        return response()->json(['data' => $tenantData]);
    }

    /**
     * Store a newly created Business (Tenant).
     * Accessible only by Super Admin.
     */
    public function store(Request $request)
    {
        // In a real app, we'd check if auth()->user()->isSuperAdmin()
        // For prototype, we assume the Super Admin is calling this.
        
        $validated = $request->validate([
            'business_name' => 'required|string|max:255',
            // Regex for PAN: 5 letters, 4 numbers, 1 letter
            'pan' => ['nullable', 'string', 'max:15', 'regex:/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/i', 'unique:tenants,pan'],
            // Check email uniqueness in users table
            'email' => 'required|email|max:255|unique:users,email',
            'address' => 'nullable|string',
            'state' => 'nullable|string|max:255',
            'city' => 'nullable|string|max:255',
            'phone' => 'nullable|string|max:20',
            'industry' => 'nullable|string|max:255',
            // Regex for GSTIN: 2 numbers, 5 letters, 4 numbers, 1 letter, 1 alphanumeric, Z, 1 alphanumeric
            'gstin' => ['nullable', 'string', 'max:15', 'regex:/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/i', 'unique:tenants,gstin'],
            'financial_year_start' => 'nullable|date',
        ]);

        \Illuminate\Support\Facades\DB::beginTransaction();

        try {
            // 1. Create the Business Owner User
            $user = \App\Models\User::create([
                'name' => 'Business Owner', // A default name, they can change it later
                'email' => $validated['email'],
                'password' => \Illuminate\Support\Facades\Hash::make('password'), // Default password
                'is_super_admin' => false,
            ]);

            // 2. Create the Tenant (this also creates the sqlite DB and runs migrations)
            $tenant = Tenant::create([
                'business_name' => $validated['business_name'],
                'pan' => $validated['pan'] ?? null,
                'address' => $validated['address'] ?? null,
                'state' => $validated['state'] ?? null,
                'city' => $validated['city'] ?? null,
                'phone' => $validated['phone'] ?? null,
                'industry' => $validated['industry'] ?? null,
                'gstin' => $validated['gstin'] ?? null,
                'financial_year_start' => $validated['financial_year_start'] ?? null,
            ]);

            // Seed default master data for this new tenant
            $tenant->run(function () {
                $now = now();
                
                // Seed Accounts
                \Illuminate\Support\Facades\DB::table('accounts')->insert([
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'code' => '4000', 'name' => 'Sales Revenue', 'type' => 'Revenue', 'created_at' => $now, 'updated_at' => $now],
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'code' => '5000', 'name' => 'Rent Expense', 'type' => 'Expense', 'created_at' => $now, 'updated_at' => $now],
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'code' => '5010', 'name' => 'Office Supplies', 'type' => 'Expense', 'created_at' => $now, 'updated_at' => $now],
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'code' => '5020', 'name' => 'Software Subscriptions', 'type' => 'Expense', 'created_at' => $now, 'updated_at' => $now],
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'code' => '1000', 'name' => 'Cash', 'type' => 'Asset', 'created_at' => $now, 'updated_at' => $now],
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'code' => '2000', 'name' => 'Accounts Payable', 'type' => 'Liability', 'created_at' => $now, 'updated_at' => $now],
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'code' => '3000', 'name' => 'Owner Capital', 'type' => 'Equity', 'created_at' => $now, 'updated_at' => $now],
                ]);

                // Seed Suppliers
                \Illuminate\Support\Facades\DB::table('suppliers')->insert([
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'name' => 'Amazon Web Services', 'gstin' => '29XYZDE1234F1Z9', 'contact_person' => 'Billing Dept', 'created_at' => $now, 'updated_at' => $now],
                    ['id' => \Illuminate\Support\Str::uuid()->toString(), 'name' => 'Rajesh (Electrician)', 'gstin' => '27ABCDE1234F1Z5', 'contact_person' => 'Rajesh Kumar', 'created_at' => $now, 'updated_at' => $now],
                ]);
            });

            // 3. Link the User to the Tenant
            \Illuminate\Support\Facades\DB::table('user_tenants')->insert([
                'user_id' => $user->id,
                'tenant_id' => $tenant->id,
                'role' => 'Business Owner',
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            \Illuminate\Support\Facades\DB::commit();

            return response()->json([
                'message' => 'Business provisioned successfully',
                'data' => $tenant
            ], 201);
            
        } catch (\Exception $e) {
            \Illuminate\Support\Facades\DB::rollBack();
            return response()->json(['message' => 'Failed to provision tenant: ' . $e->getMessage()], 500);
        }
    }
}
