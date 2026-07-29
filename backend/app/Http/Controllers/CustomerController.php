<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Customer;

class CustomerController extends Controller
{
    public function index()
    {
        return response()->json(['data' => Customer::all()]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'nullable|email',
            'gstin' => 'nullable|string',
            'phone' => 'nullable|string',
            'address' => 'nullable|string'
        ]);

        $customer = Customer::create($validated);
        
        return response()->json([
            'message' => 'Customer created successfully',
            'data' => $customer
        ], 201);
    }
}
