<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class AuthController extends Controller
{
    public function login(Request $request)
    {
        $credentials = $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        if (!Auth::attempt($credentials)) {
            return response()->json(['message' => 'Invalid credentials'], 401);
        }

        $user = Auth::user();
        $token = $user->createToken('auth_token')->plainTextToken;

        $tenantId = null;
        $tenantName = null;
        if (!$user->is_super_admin) {
            $pivot = DB::table('user_tenants')->where('user_id', $user->id)->first();
            if ($pivot) {
                $tenantId = $pivot->tenant_id;
                $tenantInfo = DB::table('tenants')->where('id', $tenantId)->first();
                if ($tenantInfo) {
                    $tenantData = json_decode($tenantInfo->data, true);
                    $tenantName = $tenantData['company_name'] ?? 'Your Company';
                }
            }
        }

        return response()->json([
            'access_token' => $token,
            'token_type' => 'Bearer',
            'user' => [
                'id' => $user->id,
                'name' => $user->name,
                'email' => $user->email,
                'is_super_admin' => $user->is_super_admin,
                'tenant_id' => $tenantId,
                'tenant_name' => $tenantName,
            ]
        ]);
    }
}
