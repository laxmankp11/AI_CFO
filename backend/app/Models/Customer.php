<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Customer extends Model
{
    use HasFactory, HasUuids;
    
    protected $fillable = [
        'name', 'email', 'gstin', 'phone', 'address'
    ];

    public function invoices()
    {
        return $this->hasMany(Invoice::class);
    }
}
