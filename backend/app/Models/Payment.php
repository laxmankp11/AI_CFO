<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Payment extends Model
{
    use HasFactory, HasUuids;
    
    protected $fillable = [
        'invoice_id', 'amount', 'payment_date', 'payment_method'
    ];

    public function invoice()
    {
        return $this->belongsTo(Invoice::class);
    }
}
