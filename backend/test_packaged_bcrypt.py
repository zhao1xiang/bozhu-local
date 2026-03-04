#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包环境中的 bcrypt 支持
"""

print()
print("=" * 60)
print("测试 bcrypt 库可用性")
print("=" * 60)
print()

# 测试 1: 导入 passlib
print("[1/4] 测试 passlib...")
try:
    import passlib
    print(f"  ✓ passlib 版本: {passlib.__version__}")
except ImportError as e:
    print(f"  ✗ passlib 不可用: {e}")
    print()
    print("  解决方法: pip install passlib[bcrypt]")

print()

# 测试 2: 导入 bcrypt
print("[2/4] 测试 bcrypt...")
try:
    import bcrypt
    print(f"  ✓ bcrypt 版本: {bcrypt.__version__}")
except ImportError as e:
    print(f"  ✗ bcrypt 不可用: {e}")
    print()
    print("  解决方法: pip install bcrypt")

print()

# 测试 3: 导入 _bcrypt (C 扩展)
print("[3/4] 测试 _bcrypt (C 扩展)...")
try:
    import _bcrypt
    print(f"  ✓ _bcrypt 可用")
except ImportError as e:
    print(f"  ✗ _bcrypt 不可用: {e}")
    print()
    print("  这是 bcrypt 的 C 扩展，打包时可能缺失")

print()

# 测试 4: 测试 passlib.context
print("[4/4] 测试 passlib.context...")
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # 生成测试哈希
    test_hash = pwd_context.hash("test")
    print(f"  ✓ CryptContext 可用")
    print(f"  测试哈希: {test_hash[:50]}...")
    
    # 验证测试哈希
    if pwd_context.verify("test", test_hash):
        print(f"  ✓ 哈希验证成功")
    else:
        print(f"  ✗ 哈希验证失败")
        
except Exception as e:
    print(f"  ✗ CryptContext 不可用: {e}")

print()
print("=" * 60)
print("总结")
print("=" * 60)
print()

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    test_hash = pwd_context.hash("admin")
    
    if pwd_context.verify("admin", test_hash):
        print("✓ bcrypt 完全可用，可以正常验证密码")
    else:
        print("✗ bcrypt 验证失败")
except Exception as e:
    print(f"✗ bcrypt 不可用: {e}")
    print()
    print("打包时需要确保包含以下库：")
    print("  - passlib")
    print("  - bcrypt")
    print("  - _bcrypt (C 扩展)")

print()
