<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class TenantTaxSettingController extends Controller
{
    public function show(Request $request)
    {
        $settings = DB::table('tenant_tax_settings')->first();
        return response()->json(['data' => $settings]);
    }

    public function update(Request $request)
    {
        $validated = $request->validate([
            'is_tax_registered' => 'required|boolean',
            'tax_id_number' => 'nullable|string',
            'default_sales_tax_code' => 'nullable|string',
            'home_state' => 'nullable|string',
            'is_tax_inclusive' => 'required|boolean',
        ]);

        $existing = DB::table('tenant_tax_settings')->first();

        if ($existing) {
            DB::table('tenant_tax_settings')
                ->where('id', $existing->id)
                ->update(array_merge($validated, ['updated_at' => now()]));
        } else {
            DB::table('tenant_tax_settings')->insert(array_merge($validated, [
                'id' => Str::uuid(),
                'created_at' => now(),
                'updated_at' => now(),
            ]));
        }

        return response()->json(['message' => 'Tenant Tax Settings updated successfully']);
    }
}
