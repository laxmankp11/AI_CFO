<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class GlobalTaxRuleController extends Controller
{
    public function index()
    {
        $rules = DB::table('global_tax_rules')->get();
        return response()->json(['data' => $rules]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'tax_code' => 'required|string',
            'country' => 'required|string',
            'regime' => 'required|string',
            'components' => 'required|array',
        ]);

        DB::table('global_tax_rules')->insert([
            'id' => Str::uuid(),
            'tax_code' => $validated['tax_code'],
            'country' => $validated['country'],
            'regime' => $validated['regime'],
            'components' => json_encode($validated['components']),
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['message' => 'Global Tax Rule created successfully']);
    }
}
