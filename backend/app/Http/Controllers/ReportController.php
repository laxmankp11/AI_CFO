<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\JournalLine;
use Illuminate\Support\Facades\DB;

class ReportController extends Controller
{
    /**
     * Generate Profit and Loss Statement
     */
    public function profitAndLoss(Request $request)
    {
        // For the MVP, we aggregate all Revenue and Expense accounts
        // In a real app, we would filter by date range

        $lines = JournalLine::with('account', 'journalEntry')
            ->join('accounts', 'journal_lines.account_id', '=', 'accounts.id')
            ->select('journal_lines.*', 'accounts.name as account_name', 'accounts.type as account_type')
            ->get();

        $revenueAccounts = [];
        $expenseAccounts = [];

        $totalRevenue = 0;
        $totalExpenses = 0;

        foreach ($lines as $line) {
            $amount = (float) $line->amount;
            $type = $line->account_type;
            
            // Normalize balance (Revenue normal is Credit, Expense normal is Debit)
            if ($type === 'Revenue' || $type === 'Income') {
                $balanceChange = ($line->dc === 'credit') ? $amount : -$amount;
                
                if (!isset($revenueAccounts[$line->account_name])) {
                    $revenueAccounts[$line->account_name] = 0;
                }
                $revenueAccounts[$line->account_name] += $balanceChange;
                $totalRevenue += $balanceChange;
                
            } elseif ($type === 'Expense') {
                $balanceChange = ($line->dc === 'debit') ? $amount : -$amount;
                
                if (!isset($expenseAccounts[$line->account_name])) {
                    $expenseAccounts[$line->account_name] = 0;
                }
                $expenseAccounts[$line->account_name] += $balanceChange;
                $totalExpenses += $balanceChange;
            }
        }

        return response()->json([
            'data' => [
                'revenue' => $revenueAccounts,
                'total_revenue' => $totalRevenue,
                'expenses' => $expenseAccounts,
                'total_expenses' => $totalExpenses,
                'net_profit' => $totalRevenue - $totalExpenses
            ]
        ]);
    }
}
