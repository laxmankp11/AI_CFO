<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Invoice;
use App\Models\Payment;
use Illuminate\Support\Facades\DB;

class DashboardController extends Controller
{
    public function index()
    {
        // For MVP, we use basic queries. In a real app, this would be highly optimized.

        // Accounts Receivable: Total amount of all invoices minus all payments
        $totalInvoiced = Invoice::where('status', '!=', 'Draft')->sum('total_amount');
        $totalPaid = Payment::sum('amount');
        $accountsReceivable = $totalInvoiced - $totalPaid;

        // Unbilled Invoices: Sum of Draft invoices
        $unbilledInvoices = Invoice::where('status', 'Draft')->sum('total_amount');

        // Accounts Payable: For MVP, we don't have Purchase Bills yet. We'll return 0 or mock it.
        // Or if we have a Suppliers table, we can mock it for now.
        $accountsPayable = 0.00; // Will be implemented when Purchase module is built

        // Total Cash: Cash account balance (mocked for MVP)
        // We can fetch from Journal Entries for account 'Cash' (1000)
        $cashDebits = DB::table('journal_lines')
            ->join('accounts', 'journal_lines.account_id', '=', 'accounts.id')
            ->where('accounts.code', '1000')
            ->sum('journal_lines.debit_amount');
            
        $cashCredits = DB::table('journal_lines')
            ->join('accounts', 'journal_lines.account_id', '=', 'accounts.id')
            ->where('accounts.code', '1000')
            ->sum('journal_lines.credit_amount');
            
        $totalCash = $cashDebits - $cashCredits;

        // Recent Activity Feed
        $recentInvoices = Invoice::with('customer')->orderBy('created_at', 'desc')->take(5)->get();

        return response()->json([
            'data' => [
                'total_cash' => $totalCash,
                'accounts_receivable' => $accountsReceivable,
                'accounts_payable' => $accountsPayable,
                'unbilled_invoices' => $unbilledInvoices,
                'recent_invoices' => $recentInvoices
            ]
        ]);
    }
}
