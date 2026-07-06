<?php
declare(strict_types=1);

header('Content-Type: text/plain; charset=UTF-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  http_response_code(405);
  echo 'Only POST requests are allowed.';
  exit;
}

$receiving_email_address = 'matty.ditlhake@gmail.com';

function field(string $name): string {
  return trim((string) ($_POST[$name] ?? ''));
}

$name = field('name');
$email = field('email');
$subject = field('subject');
$message = field('message');

if ($name === '' || $email === '' || $subject === '' || $message === '') {
  http_response_code(422);
  echo 'Please complete all required fields.';
  exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
  http_response_code(422);
  echo 'Please enter a valid email address.';
  exit;
}

$clean_name = str_replace(["\r", "\n"], ' ', $name);
$clean_subject = str_replace(["\r", "\n"], ' ', $subject);
$safe_subject = 'Portfolio contact: ' . $clean_subject;
$host = preg_replace('/[^A-Za-z0-9.-]/', '', (string) ($_SERVER['HTTP_HOST'] ?? 'localhost'));
$host = $host !== '' ? $host : 'localhost';

$body = "You have a new message from your portfolio contact form.\n\n";
$body .= "Name: {$clean_name}\n";
$body .= "Email: {$email}\n";
$body .= "Subject: {$clean_subject}\n\n";
$body .= "Message:\n{$message}\n";

$headers = [
  'From: Portfolio Contact <no-reply@' . $host . '>',
  'Reply-To: ' . $clean_name . ' <' . $email . '>',
  'Content-Type: text/plain; charset=UTF-8',
  'X-Mailer: PHP/' . phpversion(),
];

$sent = mail($receiving_email_address, $safe_subject, $body, implode("\r\n", $headers));

if (!$sent) {
  http_response_code(500);
  echo 'The message could not be sent. Please email me directly at ' . $receiving_email_address . '.';
  exit;
}

echo 'OK';
