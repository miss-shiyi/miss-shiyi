# [swift的存储属性和计算属性](https://github.com/miss-shiyi/miss-shiyi/issues/4)

#### 1. 存储属性




#### 2. 计算属性
> 除了存储属性，类、结构体和枚举也能够定义计算属性，而它实际并不存储值。相反，它提供
一个读取器和一个可选的设置器来间接得到和设置其它的属性和值。
> 如果一个计算属性的设置器没有为将要被设置的值定义一个名字，那么它将被默认命名为`newValue` 。
> 如果整个` getter` 的函数体是一个单一的表达式，那么 `getter` 隐式返回这个表达式。

```swift
struct Point {
    var x = 0.0, y = 0.0
    
}

struct Size{
    var width = 0.0, height = 0.0
}

struct Rect {
    var origin = Point()
    var size = Size()
    var center: Point {
        get{
//            let centerx = origin.x + size.width / 2
//            let centery = origin.y + size.height / 2
//            return Point(x: centerx, y: centery)
            return Point(x: origin.x + size.width / 2, y: origin.y + size.height / 2)
           //或者隐式返回 Point(x: origin.x + size.width / 2, y: origin.y + size.height / 2)
        }
//        set(newcenter){
//            origin.x = newcenter.x - size.width / 2
//            origin.y = newcenter.y - size.height / 2
//        }
        set{
            origin.x = newValue.x - size.width / 2
            origin.y = newValue.y - size.height / 2
        }
    }
}

var rect = Rect(origin: Point(x: 2, y: 4), size: Size(width: 4, height: 8))
print(rect.center)

rect.center = Point(x: 6, y: 9)
print(rect.origin.x)

```