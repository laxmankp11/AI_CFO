<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Invoice extends Model
{
    use HasFactory, HasUuids;
    
    protected $fillable = [
        'customer_id', 'invoice_number', 'description', 'total_amount', 'status', 'issue_date', 'due_date'
    ];

    public function customer()
    {
        return $this->belongsTo(Customer::class);
    }
    
    public function payments()
    {
        return $this->hasMany(Payment::class);
    }
}
