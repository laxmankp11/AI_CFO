<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Payment;
use App\Models\Invoice;
use Illuminate\Support\Facades\DB;

class PaymentController extends Controller
{
    public function store(Request $request, $invoiceId)
    {
        $validated = $request->validate([
            'amount' => 'required|numeric|min:0.01',
            'payment_date' => 'required|date',
            'payment_method' => 'nullable|string'
        ]);

        $invoice = Invoice::findOrFail($invoiceId);

        DB::beginTransaction();
        try {
            $validated['invoice_id'] = $invoice->id;
            $payment = Payment::create($validated);
            
            // Check if invoice is fully paid
            $totalPaid = $invoice->payments()->sum('amount');
            if ($totalPaid >= $invoice->total_amount) {
                $invoice->update(['status' => 'Paid']);
            } else {
                // If it was just 'Draft' or 'Sent', maybe change to 'Partial' but we'll just keep it simple
                // Let's assume if any payment is made and it's not full, it's just recorded.
            }

            DB::commit();

            return response()->json([
                'message' => 'Payment recorded successfully',
                'data' => $payment
            ], 201);
            
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json(['message' => 'Payment failed', 'error' => $e->getMessage()], 500);
        }
    }
}
