<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class JournalEntryController extends Controller
{
    public function index()
    {
        $entries = DB::table('journal_entries')->orderBy('created_at', 'desc')->get();
        
        foreach ($entries as $entry) {
            $entry->lines = DB::table('journal_lines')
                ->join('accounts', 'journal_lines.account_id', '=', 'accounts.id')
                ->where('journal_entry_id', $entry->id)
                ->select('journal_lines.*', 'accounts.name as account_name', 'accounts.code as account_code')
                ->get();
        }

        return response()->json([
            'data' => $entries
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'intent' => 'required|string',
            'total_amount' => 'required|numeric|min:0',
            'line_items' => 'required|array',
            'line_items.*.account_id' => 'nullable|string',
            'line_items.*.account_name' => 'required|string',
            'line_items.*.amount' => 'required|numeric|min:0',
            'line_items.*.dc' => 'required|in:debit,credit',
            'payment_channel' => 'nullable|string',
            'narration' => 'nullable|string',
        ]);

        try {
            DB::beginTransaction();

            $journalEntryId = Str::uuid()->toString();

            DB::table('journal_entries')->insert([
                'id' => $journalEntryId,
                'entry_date' => now()->toDateString(),
                'narration' => $validated['narration'] ?? 'AI Generated Entry',
                'status' => 'Posted',
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            foreach ($validated['line_items'] as $line) {
                $accountId = $line['account_id'];
                if (!$accountId) {
                    // Try fuzzy match by name
                    $match = DB::table('accounts')
                        ->where('name', 'like', '%' . $line['account_name'] . '%')
                        ->first();
                    
                    if ($match) {
                        $accountId = $match->id;
                    } else {
                        // Create new account if not found
                        $accountId = Str::uuid()->toString();
                        $isBank = preg_match('/bank|cash|hdfc|sbi|icici/i', $line['account_name'] ?? '');
                        $maxCode = DB::table('accounts')->max('code');
                        $newCode = str_pad((int)$maxCode + 1, 4, '0', STR_PAD_LEFT);

                        DB::table('accounts')->insert([
                            'id' => $accountId,
                            'code' => $newCode,
                            'name' => $line['account_name'],
                            'type' => $isBank ? 'Asset' : 'Expense',
                            'created_at' => now(),
                            'updated_at' => now(),
                        ]);
                    }
                }

                DB::table('journal_lines')->insert([
                    'id' => Str::uuid()->toString(),
                    'journal_entry_id' => $journalEntryId,
                    'account_id' => $accountId,
                    'debit_amount' => $line['dc'] === 'debit' ? $line['amount'] : 0,
                    'credit_amount' => $line['dc'] === 'credit' ? $line['amount'] : 0,
                    'created_at' => now(),
                    'updated_at' => now(),
                ]);
            }

            DB::commit();

            return response()->json([
                'message' => 'Journal entry created successfully.',
                'journal_entry_id' => $journalEntryId
            ], 201);

        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'message' => 'Failed to create journal entry',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
