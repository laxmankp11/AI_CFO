<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

use App\Models\PurchaseBill;

class PurchaseBillController extends Controller
{
    public function index()
    {
        $bills = PurchaseBill::with('supplier')->orderBy('issue_date', 'desc')->get();
        return response()->json(['data' => $bills]);
    }
}
