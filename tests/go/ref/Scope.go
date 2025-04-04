// A Scope maintains a set of objects and links to its containing
// (parent) and contained (children) scopes. Objects may be inserted
// and looked up by name. The zero value for Scope is a ready-to-use
// empty scope.
package MyScope

import (
	"go/constant"
	"go/token"
)

type Scope struct {
	parent   *Scope
	children []*Scope
	number   int               // parent.children[number-1] is this scope; 0 if there is no parent
	elems    map[string]Object // lazily allocated
	pos, end token.Pos         // scope extent; may be invalid
	comment  string            // for debugging only
	isFunc   bool              // set if this is a function scope (internal use only)
}

func (s *Scope) Lookup(name string) Object {
	obj := resolve(name, s.elems[name])
	// Hijack Lookup for "any": with gotypesalias=1, we want the Universe to
	// return an Alias for "any", and with gotypesalias=0 we want to return
	// the legacy representation of aliases.
	//
	// This is rather tricky, but works out after auditing of the usage of
	// s.elems. The only external API to access scope elements is Lookup.
	//
	// TODO: remove this once gotypesalias=0 is no longer supported.
	if obj == universeAnyAlias && !aliasAny() {
		return universeAnyNoAlias
	}
	return obj
}

type Object interface {
	Parent() *Scope // scope in which this object is declared; nil for methods and struct fields
	Pos() token.Pos // position of object identifier in declaration
	Pkg() *Package  // package to which this object belongs; nil for labels and objects in the Universe scope
	Name() string   // package local object name
	Type() Type     // object type
	Exported() bool // reports whether the name starts with a capital letter
	Id() string     // object name if exported, qualified name if not exported (see func Id)

	// String returns a human-readable string of the object.
	String() string

	// order reflects a package-level object's source order: if object
	// a is before object b in the source, then a.order() < b.order().
	// order returns a value > 0 for package-level objects; it returns
	// 0 for all other objects (including objects in file scopes).
	order() uint32

	// color returns the object's color.
	color() color

	// setType sets the type of the object.
	setType(Type)

	// setOrder sets the order number of the object. It must be > 0.
	setOrder(uint32)

	// setColor sets the object's color. It must not be white.
	setColor(color color)

	// setParent sets the parent scope of the object.
	setParent(*Scope)

	// sameId reports whether obj.Id() and Id(pkg, name) are the same.
	// If foldCase is true, names are considered equal if they are equal with case folding
	// and their packages are ignored (e.g., pkg1.m, pkg1.M, pkg2.m, and pkg2.M are all equal).
	sameId(pkg *Package, name string, foldCase bool) bool

	// scopePos returns the start position of the scope of this Object
	scopePos() token.Pos

	// setScopePos sets the start position of the scope for this Object.
	setScopePos(pos token.Pos)
}

type object struct {
	parent    *Scope
	pos       token.Pos
	pkg       *Package
	name      string
	typ       Type
	order_    uint32
	color_    color
	scopePos_ token.Pos
}

type PkgName struct {
	object
	imported *Package
	used     bool // set if the package was used
}

type Const struct {
	object
	val constant.Value
}

type TypeName struct {
	object
}

type Var struct {
	object
	embedded bool // if set, the variable is an embedded struct field, and name is the type name
	isField  bool // var is struct field
	used     bool // set if the variable was used
	origin   *Var // if non-nil, the Var from which this one was instantiated
}

type Func struct {
	object
	hasPtrRecv_ bool  // only valid for methods that don't have a type yet; use hasPtrRecv() to read
	origin      *Func // if non-nil, the Func from which this one was instantiated
}

type Builtin struct {
	object
	id builtinId
}

type Nil struct {
	object
}

// A Type represents a type of Go.
// All types implement the Type interface.
type Type interface {
	// Underlying returns the underlying type of a type.
	// Underlying types are never Named, TypeParam, or Alias types.
	//
	// See https://go.dev/ref/spec#Underlying_types.
	Underlying() Type

	// String returns a string representation of a type.
	String() string
}

// A Signature represents a (non-builtin) function or method type.
// The receiver is ignored when comparing signatures for identity.
type Signature struct {
	// We need to keep the scope in Signature (rather than passing it around
	// and store it in the Func Object) because when type-checking a function
	// literal we call the general type checker which returns a general Type.
	// We then unpack the *Signature and use the scope for the literal body.
	rparams  *TypeParamList // receiver type parameters from left to right, or nil
	tparams  *TypeParamList // type parameters from left to right, or nil
	scope    *Scope         // function scope for package-local and non-instantiated signatures; nil otherwise
	recv     *Var           // nil if not a method
	params   *Tuple         // (incoming) parameters from left to right; or nil
	results  *Tuple         // (outgoing) results from left to right; or nil
	variadic bool           // true if the last parameter's type is of the form ...T (or string, for append built-in only)
}
