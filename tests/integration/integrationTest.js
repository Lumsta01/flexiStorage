const AWS = require('aws-sdk');

// Configure AWS region
AWS.config.update({
    region: "eu-west-1", // Replace with your AWS region
});

// Set up service clients
const dynamoDb = new AWS.DynamoDB.DocumentClient();
const lambda = new AWS.Lambda();

// Test data for payment
const testPaymentData = {
    billingOption: "Yearly",
    amount: 299.99,
    paymentMethod: "PayPal",
};

// Test function
async function testCreatePayment() {
    try {
        // Simulate API call by invoking the Lambda function
        const payload = {
            httpMethod: "POST",
            path: "/create-payment",
            body: JSON.stringify(testPaymentData),
        };

        const result = await lambda.invoke({
            FunctionName: "PaymentsHandler", // Replace with your Lambda function name
            Payload: JSON.stringify(payload),
        }).promise();

        console.log("Lambda Response:", JSON.parse(result.Payload));

        // Verify data in DynamoDB
        const { Items } = await dynamoDb.scan({ TableName: "Payments" }).promise();
        console.log("DynamoDB Data:", Items);
    } catch (error) {
        console.error("Error during test:", error);
    }
}

// Run the test
testCreatePayment();
