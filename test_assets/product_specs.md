# Product Specifications - E-Shop Checkout System

## Overview
This document outlines the feature specifications and business rules for the E-Shop Checkout page.

## Discount Codes

### SAVE15 Discount Code
- **Code**: SAVE15
- **Discount**: 15% off the subtotal
- **Application**: The discount code SAVE15 applies a 15% discount to the cart subtotal
- **Validation**: Code must be entered in uppercase (case-insensitive matching is acceptable)
- **Display**: Discount amount should be displayed in the cart summary section

## Shipping Options

### Standard Shipping
- **Cost**: Free
- **Description**: Standard shipping is free for all orders
- **Delivery Time**: 5-7 business days

### Express Shipping
- **Cost**: $10.00
- **Description**: Express shipping costs $10
- **Delivery Time**: 2-3 business days
- **Note**: Express shipping is an additional charge applied to the order total

## Cart Features

### Add to Cart Functionality
- Users can add items to their cart
- Cart displays item names and prices
- Cart summary shows:
  - Subtotal (sum of all items)
  - Applied discount (if any)
  - Shipping cost
  - Total amount

### Cart Summary Display
- Must show all cart items with names and prices
- Must display subtotal calculation
- Must show discount amount (if applied)
- Must display shipping cost based on selected method
- Must show final total (subtotal - discount + shipping)

## User Details Form

### Required Fields
All fields in the user details form are required and must be validated:

1. **Full Name**
   - Minimum length: 2 characters
   - Must contain alphabetic characters
   - Required field

2. **Email Address**
   - Must be a valid email format
   - Must contain @ symbol and domain
   - Required field
   - Validation: Standard email regex pattern

3. **Phone Number**
   - Must be 10-15 digits
   - Numeric only
   - Required field
   - Pattern: [0-9]{10,15}

4. **Shipping Address**
   - Minimum length: 10 characters
   - Required field
   - Multi-line text input

5. **City**
   - Minimum length: 2 characters
   - Required field
   - Alphabetic characters

6. **ZIP Code**
   - Must be 5-10 digits
   - Numeric only
   - Required field
   - Pattern: [0-9]{5,10}

### Form Validation Rules
- All required fields must be filled before form submission
- Email must match standard email format
- Phone number must be 10-15 digits
- ZIP code must be 5-10 digits
- Address must be at least 10 characters long
- Validation errors should be displayed inline below each field
- Form submission should be prevented if validation fails

## Shipping Method Selection
- Users must select either Standard or Express shipping
- Default selection: Standard (Free)
- Selection should update the shipping cost in real-time
- Shipping cost should be reflected in the total calculation immediately

## Order Completion
- Order can only be completed when:
  - All form fields are valid
  - At least one item is in the cart
  - Shipping method is selected
- Upon successful validation, order should be processed
- User should receive confirmation of order completion

## UI/UX Requirements
- Responsive design for mobile and desktop
- Clear error messages for validation failures
- Real-time validation feedback
- Visual indication of selected shipping method
- Discount code application feedback (success/error messages)

## Business Rules Summary
1. The discount code SAVE15 applies a 15% discount
2. Express shipping costs $10; Standard shipping is free
3. All user detail fields are required and must pass validation
4. Cart total = Subtotal - Discount + Shipping Cost
5. Form validation must occur before order completion

