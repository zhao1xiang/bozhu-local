#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特定的 bcrypt 哈希值
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security import verify_password

# 你提供的哈希值
hash_value = "$2b$12$7xMqDiW4YlI/dXv80gtXiObTJfB4WKZNNCXWdQAEJMzSacsalp/kG"

print()
print("=" * 60)
print("测试 bcrypt 哈希值")
print("=" * 60)
print()
print(f"哈希值: {hash_value}")
print()

# 测试常见密码
test_passwords = [
    "admin",
    "admin123",
    "123456",
    "password",
    "Admin",
    "ADMIN",
    "admin123456",
    ""
]

print("测试密码列表：")
print()

found = False
for pwd in test_passwords:
    result = verify_password(pwd, hash_value)
    status = "✓ 匹配" if result else "✗ 不匹配"
    print(f"  {pwd:15} - {status}")
    if result:
        found = True
        correct_password = pwd

print()
print("=" * 60)

if found:
    print(f"✓ 找到匹配密码: '{correct_password}'")
else:
    print("✗ 未找到匹配密码")
    print()
    print("可能的原因：")
    print("  1. 密码不在测试列表中")
    print("  2. 哈希值损坏或不完整")
    print("  3. bcrypt 库版本不兼容")

print("=" * 60)
print()
